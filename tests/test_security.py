from app.core.security import hash_password, verify_password


def test_password_hash_can_be_verified() -> None:
    password = "Day22-Learning-Only!"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2id$")

    assert verify_password(
        password,
        hashed,
    ) is True

    assert verify_password(
        "wrong-password",
        hashed,
    ) is False


def test_same_password_produces_different_hashes() -> None:
    password = "Day22-Learning-Only!"

    first = hash_password(password)
    second = hash_password(password)

    assert first != second

    assert verify_password(
        password,
        first,
    ) is True

    assert verify_password(
        password,
        second,
    ) is True


def test_legacy_user_without_password_cannot_authenticate() -> None:
    assert verify_password(
        "any-password",
        None,
    ) is False

    assert verify_password(
        "any-password",
        "",
    ) is False


def test_password_whitespace_is_preserved() -> None:
    password = "  Day22-Learning-Only!  "
    hashed = hash_password(password)

    assert verify_password(
        "  Day22-Learning-Only!  ",
        hashed,
    ) is True

    assert verify_password(
        "Day22-Learning-Only!",
        hashed,
    ) is False