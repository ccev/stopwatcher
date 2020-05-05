from util.waypoints import waypoint

def delete(queries, config, deleted_cache):
    print("==========================================================================================================")
    print("")
    print("!!! Please note that these Waypoints are NOT guaranteed to be removed. Please confirm if they still exist!")
    print("You can do that by checking your Map/DB if they've been updated recently (Or just spoofing there)")
    print("")
    print("==========================================================================================================")
    print("")
    try:
        print("Deleted Portals:")
        for p_id in deleted_cache["portals"]:
            portal = queries.get_full_portal_by_id(p_id)
            print(f"  - {portal[2]}   |   {portal[0]},{portal[1]}   |   {p_id}")
    except:
        pass
    print("")
    print(f"DELETE FROM {config.db_name_portal}.ingress_portals WHERE external_id in {str(deleted_cache['portals']).replace('[', '(').replace(']',')').replace(' ', '')};")
    print("")
    print("==========================================================================================================")
    print("")
    try:
        print("Deleted Stops:")
        for s_id in deleted_cache["stops"]:
            stop = queries.get_full_stop_by_id(s_id)
            print(f"  - {stop[2]}   |   {stop[0]},{stop[1]}   |   {s_id}")
        print("")
        if config.scan_type == "mad":
            print(f"DELETE FROM {config.db_name_scan}.pokestop WHERE pokestop_id in {str(deleted_cache['stops']).replace('[', '(').replace(']',')').replace(' ', '')};")
        elif config.scan_type == "rdm":
            print(f"DELETE FROM {config.db_name_scan}.pokestop WHERE id in {str(deleted_cache['stops']).replace('[', '(').replace(']',')').replace(' ', '')};")
    except:
        pass
    print("")
    print("==========================================================================================================")
    print("")
    try:
        print("Deleted Gyms:")
        for g_id in deleted_cache["gyms"]:
            gym = queries.get_full_gym_by_id(g_id)
            print(f"  - {gym[2]}   |   {gym[0]},{gym[1]}   |   {g_id}")
        print("")
        if config.scan_type == "mad":
            print(f"DELETE FROM {config.db_name_scan}.gym WHERE gym_id in {str(deleted_cache['gyms']).replace('[', '(').replace(']',')').replace(' ', '')};")
            print("")
            print(f"DELETE FROM {config.db_name_scan}.gymdetails WHERE gym_id in {str(deleted_cache['gyms']).replace('[', '(').replace(']',')').replace(' ', '')};")
        elif config.scan_type == "rdm":
            print(f"DELETE FROM {config.db_name_scan}.gym WHERE id in {str(deleted_cache['gyms']).replace('[', '(').replace(']',')').replace(' ', '')};")
    except:
        pass
    print("")
    print("==========================================================================================================")

def compare_loop(queries, config, stops, wp_type, compare_list):
    for s_id, s_lat, s_lon, s_name, s_img in stops:
        p = queries.get_full_portal_by_id(s_id)
        #0=lat, 1=lon, 2=name, 3=img
        if p is not None:
            if (s_lat != p[0]) or (s_lon != p[1]):
                """stop = waypoint(queries, config, wp_type.lower(), s_id)
                stop.update(False)"""
                compare_list[0].append([wp_type, s_name, s_lat, s_lon, p[0], p[1]])
            if s_name != p[2]:
                stop = waypoint(queries, config, wp_type.lower(), s_id)
                stop.update(False)
                compare_list[1].append([wp_type, s_name, p[2]])

            if s_img != p[3]:
                compare_list[2].append([wp_type, s_name, p[3]])
    return compare_list

def compare(queries, config):
    print("Comparing all Stops and Gyms to your Portls now. Hold tight.")
    compare_list = [[], [], []]

    stops = queries.get_stops("")
    compare_list = compare_loop(queries, config, stops, "Stop", compare_list)

    gyms = queries.get_gyms("")
    compare_list = compare_loop(queries, config, gyms, "Gym", compare_list)

    print("")
    print("Photo updates: (Not gonna put them in your scanner DB - Just FYI)")
    for s_type, s_name, s_img_new in compare_list[2]:
        print(f"  - {s_type} {s_name}")

    print("")
    print("Title updates:")
    for s_type, s_name, s_name_new in compare_list[1]:
        print(f"  - {s_type} {s_name}  ->  {s_name_new}")

    print("")
    print("Location updates:")
    for s_type, s_name, s_lat, s_lon, s_lat_new, s_lon_new in compare_list[0]:
        print(f"  - {s_type} {s_name}:  {s_lat},{s_lon}  ->  {s_lat_new},{s_lon_new}")