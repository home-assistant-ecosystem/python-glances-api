Changes
=======

0.9.0 - 2024-11-15
------------------

- Add support for Glances containers

0.8.0 - 2024-06-09
------------------

- Add/improve support for Glances v4 container & network format and improve v4 unit tests (Thanks @wittypluck)

0.7.0 - 2024-05-21
------------------

- Add support for Glances v4 network sensors (Thanks @wittypluck)

0.6.0 - 2024-02-04
------------------

- Fix network RX and TX for Home Assistant (bytes/s) (Thanks @wittypluck)
- Reformat GPU data for Home Assistant and add unit test (Thanks @wittypluck)
- Add diskio sensors for Home Assistant (in bytes/second) (Thanks @wittypluck)
- Support for Python 3.12, pytest > 8

0.5.1 - 2024-01-11
------------------

- Add guard for glances v2 (Thanks @engrbm87)
- Add missing type hints (Thanks @engrbm87)

0.5.0 - 2023-11-17
------------------

- Deprecate support for API v2 (Thanks @engrbm87)
- Fix type hint for get_ha_sensor_data (Thanks @engrbm87)
- Add percpu data (Thanks @engrbm87)
- Update containers data key (Thanks @engrbm87)
- Add GPU sensors (Thanks @neuralyze)
- Update dependencies

0.4.3 - 2023-06-27
------------------

- Add network information to Home Assistant data (Thanks @freeDom-)
- Add uptime information to Home Assistant data (Thanks @freeDom-)
- Update dependencies

0.4.2 - 2023-05-21
------------------

- Safe access container dict when memory or cpu is not exposed (Thanks @freeDom-)

20220828 - 0.4.1
----------------

- Raise error for any not OK response code (Thanks @engrbm87)
- Update dependencies

20220819 - 0.4.0
----------------

- Add pre-definied output for Home Assistant (Thanks @engrbm87)
- Extend typing support

20220605 - 0.3.6
----------------

- Use latest httpx release (CVE-2021-41945)

20220503 - 0.3.5
----------------

- Handle TimeoutException (Thanks @b0z02003)

20220116 - 0.3.4
----------------

-  Allow using a custom external httpx client (Thanks @GuyKh)

20220104 - 0.3.3
----------------

- Support later pytest-httpx releases

20211123 - 0.3.2
----------------

- Remove version constraint of httpx

20211107 - 0.3.1
----------------

- Add exception for invalid credentials (Thanks @engrbm87)

20211106 - 0.3.0
----------------

- Migrate to pyproject style
- Mgrate to httpx

20181121 - 0.2.0
----------------
- Support for HTTP Basic authentication

20180814 - 0.1.0
----------------
- Initial release
