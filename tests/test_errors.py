import pytest

from src.core.errors import ClientError, CoreError


class TestCoreError:
    def test_message_formats_category_uppercase(self) -> None:
        error = CoreError(category="core", message="something failed")

        assert str(error) == "[CORE] something failed"

    def test_message_includes_additional_info_when_provided(self) -> None:
        error = CoreError(
            category="core",
            message="something failed",
            additional_info="extra context",
        )

        assert "extra context" in str(error)
        assert str(error) == (
            "[CORE] something failed\n\nAdditional information: extra context"
        )

    def test_message_omits_additional_info_section_when_absent(self) -> None:
        error = CoreError(category="core", message="oops")

        assert "Additional information" not in str(error)

    def test_attributes_are_preserved(self) -> None:
        error = CoreError(category="core", message="oops", additional_info="details")

        assert error.category == "core"
        assert error.message == "oops"
        assert error.additional_info == "details"

    def test_is_an_exception(self) -> None:
        with pytest.raises(CoreError):
            raise CoreError(category="core", message="boom")


class TestClientError:
    def test_uses_client_category(self) -> None:
        error = ClientError(message="docker build failed")

        assert error.category == "CLIENT"
        assert str(error) == "[CLIENT] docker build failed"

    def test_inherits_from_core_error(self) -> None:
        error = ClientError(message="docker build failed")

        assert isinstance(error, CoreError)

    def test_carries_additional_info(self) -> None:
        error = ClientError(message="failed", additional_info="exit code 1")

        assert error.additional_info == "exit code 1"
        assert "exit code 1" in str(error)
