"""
Tests for billing calculator module.
"""
import pytest
from datetime import datetime
from billing import (
    price_with_tax, apply_coupon, compute_total, booking_fee,
    compute_subtotal, convert_currency, validate_coupon, split_payment,
    parse_iso_date, compute_refund, bulk_discount, compute_bulk_total,
    tax_breakdown, validate_tax_number, apply_dynamic_tax,
    loyalty_points_earned, apply_loyalty_discount, cap_price,
    round_money, is_weekend_rate
)


class TestPriceWithTax:
    def test_positive_value(self):
        assert price_with_tax(100.0) == 121.0

    def test_zero_returns_zero(self):
        assert price_with_tax(0.0) == 0.0

    @pytest.mark.parametrize("negative", [-1.0, -100])
    def test_negative_raises(self, negative):
        with pytest.raises(ValueError):
            price_with_tax(negative)


class TestApplyCoupon:
    def test_valid_coupon(self):
        assert apply_coupon(100.0, "SPORT10") == 90.0
        assert apply_coupon(100.0, "NEWUSER5") == 95.0
        assert apply_coupon(100.0, "BLACKFRIDAY") == 75.0

    def test_invalid_coupon(self):
        assert apply_coupon(100.0, "INVALID") == 100.0
        assert apply_coupon(100.0, None) == 100.0

    def test_case_insensitive(self):
        assert apply_coupon(100.0, "sport10") == 90.0
        assert apply_coupon(100.0, "Sport10") == 90.0


class TestComputeSubtotal:
    def test_positive_quantity(self):
        assert compute_subtotal(10.0, 2) == 20.0

    def test_zero_quantity_raises(self):
        with pytest.raises(ValueError):
            compute_subtotal(10.0, 0)

    def test_negative_quantity_raises(self):
        with pytest.raises(ValueError):
            compute_subtotal(10.0, -1)


class TestBookingFee:
    def test_positive_quantity(self):
        assert booking_fee(2) == 1.0

    def test_zero_quantity(self):
        assert booking_fee(0) == 0.0

    def test_negative_quantity(self):
        assert booking_fee(-2) == -1.0


class TestComputeTotal:
    def test_happy_flow_eur(self):
        assert compute_total(10.0, 2) == 25.41

    def test_happy_flow_with_coupon(self):
        assert compute_total(10.0, 2, "SPORT10") == 22.87

    def test_zero_quantity_raises(self):
        with pytest.raises(ValueError):
            compute_total(10.0, 0)

    def test_negative_quantity_raises(self):
        with pytest.raises(ValueError):
            compute_total(10.0, -1)


class TestValidateCoupon:
    def test_valid_coupons(self):
        assert validate_coupon("SPORT10")
        assert validate_coupon("NEWUSER5")
        assert validate_coupon("BLACKFRIDAY")

    def test_invalid_coupons(self):
        assert not validate_coupon("INVALID")
        assert not validate_coupon("")

    def test_case_insensitive(self):
        assert validate_coupon("sport10")
        assert validate_coupon("Sport10")


class TestSplitPayment:
    def test_even_split(self):
        assert split_payment(100.0, 2) == [50.0, 50.0]

    def test_uneven_split(self):
        assert split_payment(100.0, 3) == [33.33, 33.33, 33.34]

    def test_invalid_parts(self):
        with pytest.raises(ValueError):
            split_payment(100.0, 0)
        with pytest.raises(ValueError):
            split_payment(100.0, -1)

    def test_small_amount(self):
        assert split_payment(0.01, 3) == [0.0, 0.0, 0.01]


class TestConvertCurrency:
    def test_supported_currencies(self):
        assert convert_currency(100.0, "USD") == 108.70
        assert convert_currency(100.0, "GBP") == 86.96

    def test_unsupported_currency(self):
        with pytest.raises(KeyError):
            convert_currency(100.0, "JPY")

    def test_case_insensitive(self):
        assert convert_currency(100.0, "usd") == 108.70
        assert convert_currency(100.0, "Usd") == 108.70


class TestParseIsoDate:
    def test_valid_date(self):
        date = parse_iso_date("2024-03-20")
        assert isinstance(date, datetime)
        assert date.year == 2024
        assert date.month == 3
        assert date.day == 20

    def test_invalid_date(self):
        with pytest.raises(ValueError):
            parse_iso_date("invalid-date")


class TestComputeRefund:
    def test_valid_percentages(self):
        assert compute_refund(100.0, 0.5) == 50.0
        assert compute_refund(100.0, 1.0) == 100.0
        assert compute_refund(100.0, 0.0) == 0.0

    def test_invalid_percentages(self):
        with pytest.raises(ValueError):
            compute_refund(100.0, 1.1)
        with pytest.raises(ValueError):
            compute_refund(100.0, -0.1)

    def test_zero_amount(self):
        assert compute_refund(0.0, 0.5) == 0.0


class TestBulkDiscount:
    def test_discount_levels(self):
        assert bulk_discount(25) == 0.15
        assert bulk_discount(15) == 0.08
        assert bulk_discount(5) == 0.0

    def test_edge_cases(self):
        assert bulk_discount(20) == 0.15
        assert bulk_discount(10) == 0.08
        assert bulk_discount(9) == 0.0


class TestComputeBulkTotal:
    def test_with_discount(self):
        assert compute_bulk_total(10.0, 25) == 257.13

    def test_without_discount(self):
        assert compute_bulk_total(10.0, 5) == 60.5

    def test_with_partial_discount(self):
        assert compute_bulk_total(10.0, 15) == 166.98

    def test_zero_quantity_raises(self):
        with pytest.raises(ValueError):
            compute_bulk_total(10.0, 0)


class TestTaxBreakdown:
    def test_breakdown(self):
        net, tax = tax_breakdown(100.0)
        assert net == 100.0
        assert tax == 21.0

    def test_zero_amount(self):
        net, tax = tax_breakdown(0.0)
        assert net == 0.0
        assert tax == 0.0

    def test_negative_amount(self):
        net, tax = tax_breakdown(-100.0)
        assert net == -100.0
        assert tax == -21.0


class TestValidateTaxNumber:
    def test_valid_tax_number(self):
        assert validate_tax_number("LV1234567890")

    def test_invalid_tax_number(self):
        assert not validate_tax_number("LV123")
        assert not validate_tax_number("12345678901")
        assert not validate_tax_number("")

    def test_case_sensitive(self):
        assert not validate_tax_number("lv1234567890")


class TestApplyDynamicTax:
    def test_latvian_tax(self):
        assert apply_dynamic_tax(100.0, "LV") == 121.0

    def test_other_country_tax(self):
        assert apply_dynamic_tax(100.0, "EE") == 120.0

    def test_case_insensitive(self):
        assert apply_dynamic_tax(100.0, "lv") == 121.0
        assert apply_dynamic_tax(100.0, "ee") == 120.0

    def test_zero_amount(self):
        assert apply_dynamic_tax(0.0, "LV") == 0.0


class TestLoyaltyPoints:
    def test_points_earned(self):
        assert loyalty_points_earned(100.0) == 2

    def test_loyalty_discount(self):
        assert apply_loyalty_discount(100.0, 50) == 99.50
        assert apply_loyalty_discount(100.0, 10000) == 0.0

    def test_zero_amount(self):
        assert loyalty_points_earned(0.0) == 0

    def test_negative_points(self):
        assert apply_loyalty_discount(100.0, -50) == 100.5


class TestCapPrice:
    def test_below_cap(self):
        assert cap_price(50.0, 100.0) == 50.0

    def test_above_cap(self):
        assert cap_price(150.0, 100.0) == 100.0

    def test_equal_to_cap(self):
        assert cap_price(100.0, 100.0) == 100.0

    def test_negative_values(self):
        assert cap_price(-50.0, 100.0) == -50.0
        assert cap_price(50.0, -100.0) == -100.0


class TestRoundMoney:
    def test_rounding(self):
        assert round_money(10.555, 2) == 10.56
        assert round_money(10.555, 1) == 10.6

    def test_negative_values(self):
        assert round_money(-10.555, 2) == -10.56
        assert round_money(-10.555, 1) == -10.6

    def test_zero_decimals(self):
        assert round_money(10.555, 0) == 11.0
        assert round_money(-10.555, 0) == -11.0

    def test_large_decimals(self):
        assert round_money(10.555, 3) == 10.555
        assert round_money(-10.555, 3) == -10.555


class TestWeekendRate:
    def test_weekend(self):
        weekend = datetime(2024, 3, 23)  # Saturday
        assert is_weekend_rate(weekend)

    def test_weekday(self):
        weekday = datetime(2024, 3, 20)  # Wednesday
        assert not is_weekend_rate(weekday)

    def test_sunday(self):
        sunday = datetime(2024, 3, 24)  # Sunday
        assert is_weekend_rate(sunday)

    def test_friday(self):
        friday = datetime(2024, 3, 22)  # Friday
        assert not is_weekend_rate(friday)