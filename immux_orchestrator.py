# Replace the original run_service_check option logic hook cleanly matching this block wrapper context:
if choice == "1":
    try:
        import immux_health_parser
        immux_health_parser.execution_monitor_loop()
    except ImportError:
        print("[-] Error mapping components: 'immux_health_parser.py' is missing from the host environment path.")
