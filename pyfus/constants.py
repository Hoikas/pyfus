#    fus - fast uru server
#    Copyright (C) 2014  Adam 'Hoikas' Johnson <AdamJohnso AT gmail DOT com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

class DiffieHellmanG:
    admin = ord('a')
    auth = 41
    game = 73
    gatekeeper = 4


class NetProtocol:
    admin = ord('a')
    auth = 10
    gatekeeper = 22
    file = 16
    lobby = ord('l')


class NetError:
    pending = -1
    success = 0

    internal_error = 1
    timeout = 2
    bad_server_data = 3
    age_not_found = 4
    connect_failed = 5
    disconnected = 6
    # Unfortunately, there is no TriStateBoolean here...
    file_not_found = 7
    old_build_id = 8
    remote_shutdown = 9
    timeout_odbc = 10
    account_already_exists = 11
    player_already_exists = 12
    account_not_found = 13
    player_not_found = 14
    invalid_parameter = 15
    name_lookup_failed = 16
    logged_in_elsewhere = 17
    vault_node_not_found = 18
    max_players_on_account = 19
    authentication_failed = 20
    state_object_not_found = 21
    login_denied = 22
    circular_reference = 23
    account_not_activated = 24
    key_already_used = 25
    key_not_found = 26
    activation_code_not_found = 27
    player_name_invalid = 28
    not_supported = 29
    service_forbidden = 30
    auth_token_too_old = 31
    must_use_gametap_client = 32
    too_many_failed_logins = 33
    gametap_connection_failed = 34
    gametap_too_many_auth_options = 35
    gametap_missing_parameter = 36
    gametap_server_error = 37
    account_banned = 38
    kicked_by_ccr = 39
    score_wrong_type = 40
    score_not_enough_points = 41
    score_already_exists = 42
    score_no_data_found = 43
    invite_no_matching_player = 44
    invite_too_many_hoods = 45
    need_to_pay = 46
    server_busy = 47
    vault_node_access_violation = 48
