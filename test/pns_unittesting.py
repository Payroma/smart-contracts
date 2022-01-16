import os
import unittest
os.chdir('..')


# Configuration
contract_name = "PNSProtocol"
constructor_args = ()
contract_file_name = "PNSProtocol.sol"
debugging = True


# Deployment
from deploy import w3, run
contract = run(contract_name, constructor_args, contract_file_name)


def get_users(
        status: bool, random_users: bool = True,
        count: int = len(w3.eth.accounts), ignore: list = [0]
) -> tuple:
    users = []
    addresses = []
    statuses = []

    for i in range(count):
        if i in ignore:
            continue
        users.append('payroma%s' % i)
        addresses.append(w3.eth.account.create().address if random_users else w3.eth.accounts[i])
        statuses.append(status)

    return users, addresses, statuses


def function_name(text: str):
    print(f"[ + ] Start for: {text}")


# Testing
class MyTestCase(unittest.TestCase):
    def test_initial_details(self):
        function_name('initial_details')

        username = "payroma"

        # Task
        owner = contract.functions.owner().call()
        is_reserved = contract.functions.isReserved(username).call()
        is_recorded = contract.functions.isRecorded(username).call()
        get_by_name = contract.functions.getByName(username).call()
        get_by_address = contract.functions.getByAddress(owner).call()
        users_count = contract.functions.usersCount().call()

        # Debugging
        if debugging:
            print(f"""
            owner: {owner}
            is_reserved: {is_reserved}
            is_recorded: {is_recorded}
            get_by_name: {get_by_name}
            get_by_address: {get_by_address}
            users_count: {users_count}
            """)

        # Test
        self.assertEqual(owner, w3.eth.default_account)
        self.assertFalse(is_reserved)
        self.assertTrue(is_recorded)
        self.assertEqual(get_by_name[0], owner)
        self.assertTrue(get_by_name[1])
        self.assertFalse(get_by_name[2])
        self.assertEqual(get_by_address[0], username)
        self.assertTrue(get_by_address[1])
        self.assertFalse(get_by_address[2])
        self.assertAlmostEqual(users_count, 1)

    def _test_new_record(self):
        function_name('new_record')

        # Settings
        name = 'payroma%s'
        # name = 'Payroma%s'                      # test username uppercase
        # name = 'payrom' + ('a' * 34) + '%s'     # test username exceeds 40 characters
        users = w3.eth.accounts[1:]
        # users = w3.eth.accounts     # test sender already recorded before

        for index, address in enumerate(users):
            # Task
            username = name % index
            # username = 'payroma'  # test username already taken
            w3.eth.default_account = address
            is_recorded = contract.functions.isRecorded(username).call()
            get_by_name = contract.functions.getByName(username).call()
            get_by_address = contract.functions.getByAddress(address).call()
            users_count = contract.functions.usersCount().call()
            contract.functions.newRecord(username).transact()
            is_recorded_expected = contract.functions.isRecorded(username).call()
            get_by_name_expected = contract.functions.getByName(username).call()
            get_by_address_expected = contract.functions.getByAddress(address).call()
            users_count_expected = contract.functions.usersCount().call()

            # Debugging
            if debugging:
                print(f"""
                username: {username}
                address: {address}
                is_recorded: {is_recorded}
                is_recorded_expected: {is_recorded_expected}
                get_by_name: {get_by_name}
                get_by_name_expected: {get_by_name_expected}
                get_by_address: {get_by_address}
                get_by_address_expected: {get_by_address_expected}
                users_count: {users_count}
                users_count_expected: {users_count_expected}
                """)

            # Test
            self.assertFalse(is_recorded)
            self.assertEqual(get_by_name[0], "0x0000000000000000000000000000000000000000")
            self.assertFalse(get_by_name[1])
            self.assertFalse(get_by_name[2])
            self.assertEqual(get_by_address[0], "")
            self.assertFalse(get_by_address[1])
            self.assertFalse(get_by_address[2])
            self.assertTrue(is_recorded_expected)
            self.assertEqual(get_by_name_expected[0], address)
            self.assertFalse(get_by_name_expected[1])
            self.assertFalse(get_by_name_expected[2])
            self.assertEqual(get_by_address_expected[0], username)
            self.assertFalse(get_by_address_expected[1])
            self.assertFalse(get_by_address_expected[2])
            self.assertAlmostEqual(users_count_expected, users_count + 1)

    def _test_transfer_username(self):
        function_name('transfer_username')

        # Settings
        username = 'payroma'
        owner = w3.eth.default_account
        receipt = w3.eth.accounts[1]
        # w3.eth.default_account = receipt                      # test sender does not have username
        # contract.functions.newRecord(username).transact()     # test username already taken
        # contract.functions.newRecord("payroma2").transact()   # test newOwner already recorded
        # w3.eth.default_account = owner                        # re-switch to the owner

        # Task
        get_by_name_owner = contract.functions.getByName(username).call()
        get_by_address_owner = contract.functions.getByAddress(owner).call()
        get_by_address_receipt = contract.functions.getByAddress(receipt).call()
        contract.functions.transferUsername(receipt).transact()
        get_by_name_owner_expected = contract.functions.getByName(username).call()
        get_by_address_owner_expected = contract.functions.getByAddress(owner).call()
        get_by_address_receipt_expected = contract.functions.getByAddress(receipt).call()

        # Debugging
        if debugging:
            print(f"""
            username: {username}
            owner: {owner}
            receipt: {receipt}
            get_by_name_owner: {get_by_name_owner}
            get_by_name_owner_expected: {get_by_name_owner_expected}
            get_by_address_owner: {get_by_address_owner}
            get_by_address_owner_expected: {get_by_address_owner_expected}
            get_by_address_receipt: {get_by_address_receipt}
            get_by_address_receipt_expected: {get_by_address_receipt_expected}
            """)

        # Test
        self.assertEqual(get_by_name_owner[0], owner)
        self.assertTrue(get_by_name_owner[1])
        self.assertFalse(get_by_name_owner[2])
        self.assertEqual(get_by_address_owner[0], username)
        self.assertTrue(get_by_address_owner[1])
        self.assertFalse(get_by_address_owner[2])
        self.assertEqual(get_by_address_receipt[0], "")
        self.assertFalse(get_by_address_receipt[1])
        self.assertFalse(get_by_address_receipt[2])
        self.assertEqual(get_by_name_owner_expected[0], receipt)
        self.assertTrue(get_by_name_owner_expected[1])
        self.assertFalse(get_by_name_owner_expected[2])
        self.assertEqual(get_by_address_owner_expected[0], "")
        self.assertFalse(get_by_address_owner_expected[1])
        self.assertFalse(get_by_address_owner_expected[2])
        self.assertEqual(get_by_address_receipt_expected[0], username)
        self.assertTrue(get_by_address_receipt_expected[1])
        self.assertFalse(get_by_address_receipt_expected[2])

    def _test_set_verified(self):
        function_name('set_verified')

        # Settings
        username = 'payroma'
        # username = 'payroma2'       # test username is not recorded
        owner = w3.eth.default_account
        # w3.eth.default_account = w3.eth.accounts[1]       # calling without owner permission
        state = False
        # contract.functions.setScammer(username, owner, True).transact()     # test scammer cannot verify

        # Task
        get_by_name = contract.functions.getByName(username).call()
        get_by_address = contract.functions.getByAddress(owner).call()
        contract.functions.setVerified(username, state).transact()
        get_by_name_expected = contract.functions.getByName(username).call()
        get_by_address_expected = contract.functions.getByAddress(owner).call()

        # Debugging
        if debugging:
            print(f"""
            get_by_name: {get_by_name}
            get_by_name_expected: {get_by_name_expected}
            get_by_address: {get_by_address}
            get_by_address_expected: {get_by_address_expected}
            """)

        # Test
        self.assertEqual(get_by_name[0], owner)
        self.assertTrue(get_by_name[1])
        self.assertFalse(get_by_name[2])
        self.assertEqual(get_by_address[0], username)
        self.assertTrue(get_by_address[1])
        self.assertFalse(get_by_address[2])
        self.assertEqual(get_by_name_expected[0], owner)
        self.assertFalse(get_by_name_expected[1])
        self.assertFalse(get_by_name_expected[2])
        self.assertEqual(get_by_address_expected[0], username)
        self.assertFalse(get_by_address_expected[1])
        self.assertFalse(get_by_address_expected[2])

    def _test_set_scammer(self):
        function_name('set_scammer')

        # Settings
        username = 'payroma'
        # username = 'payroma2'       # test new username for address already recorded
        new_username = 'payroma3'
        owner = w3.eth.default_account
        new_user_address = '0x0a88952b2d1CDd84DDDFe9501285d92a8C67cB70'
        # w3.eth.default_account = w3.eth.accounts[1]       # calling without owner permission
        state = True

        # Task
        get_by_name = contract.functions.getByName(username).call()
        get_by_address = contract.functions.getByAddress(owner).call()
        users_count = contract.functions.usersCount().call()
        contract.functions.setScammer(username, owner, state).transact()
        get_by_name_expected = contract.functions.getByName(username).call()
        get_by_address_expected = contract.functions.getByAddress(owner).call()
        new_user_get_by_name = contract.functions.getByName(new_username).call()
        new_user_get_by_address = contract.functions.getByAddress(new_user_address).call()
        contract.functions.setScammer(new_username, new_user_address, state).transact()
        new_user_get_by_name_expected = contract.functions.getByName(new_username).call()
        new_user_get_by_address_expected = contract.functions.getByAddress(new_user_address).call()
        users_count_expected = contract.functions.usersCount().call()

        # Debugging
        if debugging:
            print(f"""
            get_by_name: {get_by_name}
            get_by_name_expected: {get_by_name_expected}
            get_by_address: {get_by_address}
            get_by_address_expected: {get_by_address_expected}
            new_user_get_by_name: {new_user_get_by_name}
            new_user_get_by_name_expected: {new_user_get_by_name_expected}
            new_user_get_by_address: {new_user_get_by_address}
            new_user_get_by_address_expected: {new_user_get_by_address_expected}
            users_count: {users_count}
            users_count_expected: {users_count_expected}
            """)

        # Test
        self.assertEqual(get_by_name[0], owner)
        self.assertTrue(get_by_name[1])
        self.assertFalse(get_by_name[2])
        self.assertEqual(get_by_address[0], username)
        self.assertTrue(get_by_address[1])
        self.assertFalse(get_by_address[2])
        self.assertEqual(get_by_name_expected[0], owner)
        self.assertFalse(get_by_name_expected[1])
        self.assertTrue(get_by_name_expected[2])
        self.assertEqual(get_by_address_expected[0], username)
        self.assertFalse(get_by_address_expected[1])
        self.assertTrue(get_by_address_expected[2])
        self.assertEqual(new_user_get_by_name[0], "0x0000000000000000000000000000000000000000")
        self.assertFalse(new_user_get_by_name[1])
        self.assertFalse(new_user_get_by_name[2])
        self.assertEqual(new_user_get_by_address[0], "")
        self.assertFalse(new_user_get_by_address[1])
        self.assertFalse(new_user_get_by_address[2])
        self.assertEqual(new_user_get_by_name_expected[0], new_user_address)
        self.assertFalse(new_user_get_by_name_expected[1])
        self.assertTrue(new_user_get_by_name_expected[2])
        self.assertEqual(new_user_get_by_address_expected[0], new_username)
        self.assertFalse(new_user_get_by_address_expected[1])
        self.assertTrue(new_user_get_by_address_expected[2])
        self.assertAlmostEqual(users_count_expected, users_count + 1)

    def _test_reserve_users(self):
        function_name('reserve_users')

        # Settings
        count = 10
        # count = 101       # test exceeds 100 users
        status = True
        users, _, statuses = get_users(status=status, count=count)
        # statuses.pop()    # test mismatch between users and statuses count
        # w3.eth.default_account = w3.eth.accounts[1]       # calling without owner permission

        # Task
        contract.functions.reserveUsers(users, statuses).transact()

        # Test
        for username in users:
            is_reserved = contract.functions.isReserved(username).call()

            # Debugging
            if debugging:
                print(f"""
                username: {username}
                is_reserved: {is_reserved}
                """)

            self.assertEqual(is_reserved, status)

    def _test_set_multi_verified(self):
        function_name('set_multi_verified')

        # Settings
        owner = w3.eth.default_account
        # owner = w3.eth.accounts[1]       # calling without owner permission
        status = True
        users, addresses, statuses = get_users(status=status, random_users=False)
        # statuses.pop()    # test mismatch between users and statuses count

        # Task
        for username, address in zip(users, addresses):
            w3.eth.default_account = address
            contract.functions.newRecord(username).transact()
        w3.eth.default_account = owner
        contract.functions.setMultiVerified(users, statuses).transact()

        # Test
        for username, address in zip(users, addresses):
            get_by_name = contract.functions.getByName(username).call()
            get_by_address = contract.functions.getByAddress(address).call()

            # Debugging
            if debugging:
                print(f"""
                username: {username}
                address: {address}
                get_by_name: {get_by_name}
                get_by_address: {get_by_address}
                """)

            self.assertEqual(get_by_name[0], address)
            self.assertTrue(get_by_name[1])
            self.assertFalse(get_by_name[2])
            self.assertEqual(get_by_address[0], username)
            self.assertTrue(get_by_address[1])
            self.assertFalse(get_by_address[2])

    def _test_set_multi_scammers(self):
        function_name('set_multi_scammers')

        # Settings
        count = 10
        status = True
        users, addresses, statuses = get_users(status=status, count=count)
        # statuses.pop()    # test mismatch between users and statuses count
        # w3.eth.default_account = w3.eth.accounts[1]       # calling without owner permission

        # Task
        contract.functions.setMultiScammers(users, addresses, statuses).transact()

        # Test
        for username, address in zip(users, addresses):
            get_by_name = contract.functions.getByName(username).call()
            get_by_address = contract.functions.getByAddress(address).call()

            # Debugging
            if debugging:
                print(f"""
                username: {username}
                address: {address}
                get_by_name: {get_by_name}
                get_by_address: {get_by_address}
                """)

            self.assertEqual(get_by_name[0], address)
            self.assertFalse(get_by_name[1])
            self.assertTrue(get_by_name[2])
            self.assertEqual(get_by_address[0], username)
            self.assertFalse(get_by_address[1])
            self.assertTrue(get_by_address[2])


if __name__ == '__main__':
    unittest.main()
