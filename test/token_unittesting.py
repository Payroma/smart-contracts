from web3 import Web3
from typing import Union
import os
import time
import unittest
os.chdir('..')


# Configuration
contract_name = "PayromaToken"
constructor_args = ()
contract_file_name = "Token.sol"
debugging = True


# Deployment
from deploy import w3, run
pya_contract = run(contract_name, constructor_args, contract_file_name)


def function_name(text: str):
    print(f"[ + ] Start for: {text}")


def to_ether(value: int) -> Union[int, float]:
    return Web3.fromWei(value, 'ether') if value > 0 else 0


def to_wei(value: Union[int, float]) -> int:
    return Web3.toWei(value, 'ether') if value > 0 else 0


# Testing
class MyTestCase(unittest.TestCase):
    def _test_token_details(self):
        function_name('token_details')

        user1 = w3.eth.accounts[1]
        user2 = w3.eth.accounts[2]

        # Task
        owner = pya_contract.functions.owner().call()
        name = pya_contract.functions.name().call()
        symbol = pya_contract.functions.symbol().call()
        decimals = pya_contract.functions.decimals().call()
        total_supply = pya_contract.functions.totalSupply().call()
        balance = pya_contract.functions.balanceOf(user1).call()
        allowance = pya_contract.functions.allowance(user2, user1).call()
        inflation_rate_annually = pya_contract.functions.inflationRateAnnually().call()
        inflation_duration_end_date = pya_contract.functions.inflationDurationEndDate().call()
        available_to_mint_current_year = pya_contract.functions.availableToMintCurrentYear().call()

        # Debugging
        if debugging:
            print(f"""
            owner: {owner}
            name: {name}
            symbol: {symbol}
            decimals: {decimals}
            total_supply: {to_ether(total_supply)}
            balance: {to_ether(balance)} of {user1}
            allowance: {to_ether(allowance)} of {user2} to {user1}
            inflation_rate_annually: {inflation_rate_annually}
            inflation_duration_end_date: {inflation_duration_end_date}
            available_to_mint_current_year: {to_ether(available_to_mint_current_year)}
            """)

        # Network test
        self.assertEqual(owner, w3.eth.default_account)
        self.assertEqual(name, 'Payroma Wallet')
        self.assertEqual(symbol, 'PYA')
        self.assertEqual(decimals, 18)
        self.assertEqual(total_supply, to_wei(20000000))
        self.assertEqual(balance, 0)
        self.assertEqual(allowance, 0)
        self.assertEqual(inflation_rate_annually, 5)
        self.assertEqual(inflation_duration_end_date, 0)
        self.assertEqual(available_to_mint_current_year, to_wei(1000000))

    def _test_transfer(self):
        function_name('transfer')

        # Settings
        sender = w3.eth.default_account
        recipient = w3.eth.accounts[2]
        # recipient = '0x0000000000000000000000000000000000000000'    # test send to 0 address
        amount = to_wei(1000000)
        # amount = pya_contract.functions.balanceOf(sender).call() + 1  # test send amount over balance
        attempts = 20

        for i in range(attempts):
            # Task
            sender_balance = pya_contract.functions.balanceOf(sender).call()
            sender_balance_expected = sender_balance - amount
            recipient_balance = pya_contract.functions.balanceOf(recipient).call()
            recipient_balance_expected = recipient_balance + amount
            pya_contract.functions.transfer(recipient, amount).transact()

            # Debugging
            if debugging:
                print(f"""
                attempt: {i + 1}
                -------------
                sender_balance: {to_ether(sender_balance)}
                sender_balance_expected: {to_ether(sender_balance_expected)}
                recipient_balance: {to_ether(recipient_balance)}
                recipient_balance_expected: {to_ether(recipient_balance_expected)}
                """)

            # Test
            self.assertAlmostEqual(
                pya_contract.functions.balanceOf(sender).call(), sender_balance_expected
            )
            self.assertAlmostEqual(
                pya_contract.functions.balanceOf(recipient).call(), recipient_balance_expected
            )

    def _test_transfer_multiple(self):
        function_name('transfer_multiple')

        # Settings
        sender = w3.eth.default_account
        recipient = w3.eth.accounts[2]
        # recipient = '0x0000000000000000000000000000000000000000'    # test send to 0 address
        amount = to_wei(100000)
        # amount = pya_contract.functions.balanceOf(sender).call() + 1  # test send amount over balance
        addresses_count = 10
        # addresses_count = 101       # test exceed maximum
        amounts_count = addresses_count
        # amounts_count = addresses_count - 1     # test mismatch scenario
        attempts = 20

        for i in range(attempts):
            # Task
            sender_balance = pya_contract.functions.balanceOf(sender).call()
            sender_balance_expected = sender_balance - (amount * amounts_count)
            recipient_balance = pya_contract.functions.balanceOf(recipient).call()
            recipient_balance_expected = recipient_balance + (amount * amounts_count)
            pya_contract.functions.transferMultiple(
                [recipient] * addresses_count, [amount] * amounts_count
            ).transact()

            # Debugging
            if debugging:
                print(f"""
                attempt: {i + 1}
                -------------
                sender_balance: {to_ether(sender_balance)}
                sender_balance_expected: {to_ether(sender_balance_expected)}
                recipient_balance: {to_ether(recipient_balance)}
                recipient_balance_expected: {to_ether(recipient_balance_expected)}
                """)

            # Test
            self.assertAlmostEqual(
                pya_contract.functions.balanceOf(sender).call(), sender_balance_expected
            )
            self.assertAlmostEqual(
                pya_contract.functions.balanceOf(recipient).call(), recipient_balance_expected
            )

    def _test_transfer_from(self):
        function_name('transfer_from')

        # Settings
        owner = w3.eth.default_account
        sender = w3.eth.accounts[2]
        recipient = w3.eth.accounts[3]
        # recipient = '0x0000000000000000000000000000000000000000'    # test send to 0 address
        amount = to_wei(1000000)
        # amount = pya_contract.functions.balanceOf(owner).call() + 1  # test send amount over balance
        attempts = 20

        pya_contract.functions.approve(sender, amount * attempts).transact()  # approve required
        w3.eth.default_account = sender  # Switch to sender account
        for i in range(attempts):
            # Task
            owner_balance = pya_contract.functions.balanceOf(owner).call()
            owner_balance_expected = owner_balance - amount
            recipient_balance = pya_contract.functions.balanceOf(recipient).call()
            recipient_balance_expected = recipient_balance + amount
            sender_allowance = pya_contract.functions.allowance(owner, sender).call()
            sender_allowance_expected = sender_allowance - amount
            pya_contract.functions.transferFrom(owner, recipient, amount).transact()

            # Debugging
            if debugging:
                print(f"""
                attempt: {i + 1}
                -------------
                owner_balance: {to_ether(owner_balance)}
                owner_balance_expected: {to_ether(owner_balance_expected)}
                recipient_balance: {to_ether(recipient_balance)}
                recipient_balance_expected: {to_ether(recipient_balance_expected)}
                sender_allowance: {to_ether(sender_allowance)}
                sender_allowance_expected: {to_ether(sender_allowance_expected)}
                """)

            # Test
            self.assertAlmostEqual(
                pya_contract.functions.balanceOf(owner).call(), owner_balance_expected
            )
            self.assertAlmostEqual(
                pya_contract.functions.balanceOf(recipient).call(), recipient_balance_expected
            )
            self.assertAlmostEqual(
                pya_contract.functions.allowance(owner, sender).call(), sender_allowance_expected
            )

    def _test_approve(self):
        function_name('approve')

        # Settings
        owner = w3.eth.default_account
        spender = w3.eth.accounts[2]
        # spender = '0x0000000000000000000000000000000000000000'    # test approve to 0 address
        amount = to_wei(1000000)
        attempts = 10

        for i in range(attempts):
            # Task
            owner_allowance = pya_contract.functions.allowance(owner, spender).call()
            owner_allowance_expected = amount
            pya_contract.functions.approve(spender, amount).transact()

            # Debugging
            if debugging:
                print(f"""
                attempt: {i + 1}
                -------------
                owner_allowance: {to_ether(owner_allowance)}
                owner_allowance_expected: {to_ether(owner_allowance_expected)}
                """)

            # Test
            self.assertAlmostEqual(
                pya_contract.functions.allowance(owner, spender).call(), owner_allowance_expected
            )

    def _test_increase_allowance(self):
        function_name('increase_allowance')

        # Settings
        owner = w3.eth.default_account
        spender = w3.eth.accounts[2]
        # spender = '0x0000000000000000000000000000000000000000'    # test approve to 0 address
        amount = to_wei(1000000)
        attempts = 10

        for i in range(attempts):
            # Task
            owner_allowance = pya_contract.functions.allowance(owner, spender).call()
            owner_allowance_expected = owner_allowance + amount
            pya_contract.functions.increaseAllowance(spender, amount).transact()

            # Debugging
            if debugging:
                print(f"""
                attempt: {i + 1}
                -------------
                owner_allowance: {to_ether(owner_allowance)}
                owner_allowance_expected: {to_ether(owner_allowance_expected)}
                """)

            # Test
            self.assertAlmostEqual(
                pya_contract.functions.allowance(owner, spender).call(), owner_allowance_expected
            )

    def _test_decrease_allowance(self):
        function_name('decrease_allowance')

        # Settings
        owner = w3.eth.default_account
        spender = w3.eth.accounts[2]
        # spender = '0x0000000000000000000000000000000000000000'    # test approve to 0 address
        amount = to_wei(1000000)
        attempts = 10

        pya_contract.functions.approve(spender, amount * attempts).transact()  # approve required
        for i in range(attempts):
            # Task
            owner_allowance = pya_contract.functions.allowance(owner, spender).call()
            owner_allowance_expected = owner_allowance - amount
            pya_contract.functions.decreaseAllowance(spender, amount).transact()

            # Debugging
            if debugging:
                print(f"""
                attempt: {i + 1}
                -------------
                owner_allowance: {to_ether(owner_allowance)}
                owner_allowance_expected: {to_ether(owner_allowance_expected)}
                """)

            # Test
            self.assertAlmostEqual(
                pya_contract.functions.allowance(owner, spender).call(), owner_allowance_expected
            )

    def _test_burn(self):
        function_name('burn')

        # Settings
        sender = w3.eth.default_account
        amount = to_wei(1000000)
        # amount = pya_contract.functions.balanceOf(sender).call() + 1  # test burn amount over balance
        attempts = 20

        for i in range(attempts):
            # Task
            sender_balance = pya_contract.functions.balanceOf(sender).call()
            sender_balance_expected = sender_balance - amount
            total_supply = pya_contract.functions.totalSupply().call()
            total_supply_expected = total_supply - amount
            pya_contract.functions.burn(amount).transact()

            # Debugging
            if debugging:
                print(f"""
                attempt: {i + 1}
                -------------
                sender_balance: {to_ether(sender_balance)}
                sender_balance_expected: {to_ether(sender_balance_expected)}
                total_supply: {to_ether(total_supply)}
                total_supply_expected: {to_ether(total_supply_expected)}
                """)

            # Test
            self.assertAlmostEqual(
                pya_contract.functions.balanceOf(sender).call(), sender_balance_expected
            )
            self.assertAlmostEqual(
                pya_contract.functions.totalSupply().call(), total_supply_expected
            )

    def _test_burn_from(self):
        function_name('burn_from')

        # Settings
        owner = w3.eth.default_account
        sender = w3.eth.accounts[2]
        amount = to_wei(1000000)
        # amount = pya_contract.functions.balanceOf(owner).call() + 1  # test send amount over balance
        attempts = 20

        pya_contract.functions.approve(sender, amount * attempts).transact()  # approve required
        w3.eth.default_account = sender  # Switch to sender account
        for i in range(attempts):
            # Task
            owner_balance = pya_contract.functions.balanceOf(owner).call()
            owner_balance_expected = owner_balance - amount
            sender_allowance = pya_contract.functions.allowance(owner, sender).call()
            sender_allowance_expected = sender_allowance - amount
            total_supply = pya_contract.functions.totalSupply().call()
            total_supply_expected = total_supply - amount
            pya_contract.functions.burnFrom(owner, amount).transact()

            # Debugging
            if debugging:
                print(f"""
                attempt: {i + 1}
                -------------
                owner_balance: {to_ether(owner_balance)}
                owner_balance_expected: {to_ether(owner_balance_expected)}
                sender_allowance: {to_ether(sender_allowance)}
                sender_allowance_expected: {to_ether(sender_allowance_expected)}
                total_supply: {to_ether(total_supply)}
                total_supply_expected: {to_ether(total_supply_expected)}
                """)

            # Test
            self.assertAlmostEqual(
                pya_contract.functions.balanceOf(owner).call(), owner_balance_expected
            )
            self.assertAlmostEqual(
                pya_contract.functions.allowance(owner, sender).call(), sender_allowance_expected
            )
            self.assertAlmostEqual(
                pya_contract.functions.totalSupply().call(), total_supply_expected
            )

    def _test_mint(self):
        function_name('mint')

        # Settings
        owner = w3.eth.default_account
        # w3.eth.default_account = w3.eth.accounts[2]  # test mint without owner permission
        mint_times = 5
        attempts = 10
        amount = to_wei(to_ether(pya_contract.functions.availableToMintCurrentYear().call()) / mint_times)
        # amount = 0  # test mint 0 amount
        # amount = to_wei(10000000)   # test mint over 5% inflation

        for i in range(attempts):
            # Task
            balance = pya_contract.functions.balanceOf(owner).call()
            balance_expected = balance + amount
            total_supply = pya_contract.functions.totalSupply().call()
            total_supply_expected = total_supply + amount
            available_to_mint = pya_contract.functions.availableToMintCurrentYear().call()
            available_to_mint_expected = available_to_mint - amount
            pya_contract.functions.mint(amount).transact()

            # Debugging
            if debugging:
                print(f"""
                attempt: {i + 1}
                -------------
                owner: {owner}
                balance: {to_ether(balance)}
                balance_expected: {to_ether(balance_expected)}
                total_supply: {to_ether(total_supply)}
                total_supply_expected: {to_ether(total_supply_expected)}
                available_to_mint: {to_ether(available_to_mint)}
                available_to_mint_expected: {to_ether(available_to_mint_expected)}
                """)

            # Test
            self.assertEqual(pya_contract.functions.balanceOf(owner).call(), balance_expected)
            self.assertEqual(pya_contract.functions.totalSupply().call(), total_supply_expected)
            self.assertEqual(
                pya_contract.functions.availableToMintCurrentYear().call(), available_to_mint_expected
            )

            if available_to_mint_expected == 0:
                current_time = time.time()
                inflation_duration_end_date = pya_contract.functions.inflationDurationEndDate().call()
                inflation_duration = (inflation_duration_end_date - current_time) + 1
                print(f"""
                [ + ] Please wait {inflation_duration} seconds to start a new duration of mint cycle
                Current Time: {time.ctime()}
                Renew Mint Time: {time.ctime(inflation_duration_end_date)}
                """)
                time.sleep(inflation_duration)
                # Do transaction to update block.timestamp
                pya_contract.functions.transfer(owner, to_wei(10)).transact()
                available_to_mint = pya_contract.functions.availableToMintCurrentYear().call()
                available_to_mint_expected = to_wei(
                    to_ether(pya_contract.functions.totalSupply().call()) * 5 / 100
                )
                amount = to_wei(to_ether(available_to_mint) / mint_times)

                self.assertEqual(available_to_mint, available_to_mint_expected)

    def _test_renounce_ownership(self):
        function_name('renounce_ownership')

        # Task
        owner = pya_contract.functions.owner().call()
        owner_expected = '0x0000000000000000000000000000000000000000'
        pya_contract.functions.renounceOwnership().transact()
        # pya_contract.functions.renounceOwnership().transact()   # test renounce as user

        # Debugging
        if debugging:
            print(f"""
            owner: {owner}
            owner_expected: {owner_expected}
            """)

        # Test
        self.assertEqual(pya_contract.functions.owner().call(), owner_expected)

    def _test_transfer_ownership(self):
        function_name('transfer_ownership')

        # Settings
        new_owner = w3.eth.accounts[2]
        # new_owner = '0x0000000000000000000000000000000000000000'    # test transfer to 0 address

        # Task
        owner = pya_contract.functions.owner().call()
        owner_expected = new_owner
        pya_contract.functions.transferOwnership(new_owner).transact()
        # pya_contract.functions.renounceOwnership().transact()   # test renounce as user

        # Debugging
        if debugging:
            print(f"""
            owner: {owner}
            owner_expected: {owner_expected}
            """)

        # Test
        self.assertEqual(pya_contract.functions.owner().call(), owner_expected)

    def _test_recover_token(self):
        function_name('recover_token')

        # Settings
        owner = w3.eth.default_account
        amount = to_wei(1000000)

        # Task
        # Create token and transfer amount to pya token for recover it later
        pya2_contract = run(contract_name, constructor_args, contract_file_name)
        owner_balance = pya2_contract.functions.balanceOf(owner).call()
        owner_balance_expected = owner_balance - amount
        pya_balance = pya2_contract.functions.balanceOf(pya_contract.address).call()
        pya_balance_expected = pya_balance + amount
        pya2_contract.functions.transfer(pya_contract.address, amount).transact()

        # Debugging
        if debugging:
            print(f"""
            Before Recover
            ---------------
            owner_balance: {to_ether(owner_balance)}
            owner_balance_expected: {to_ether(owner_balance_expected)}
            pya_balance: {to_ether(pya_balance)}
            pya_balance_expected: {to_ether(pya_balance_expected)}
            """)

        # Test
        self.assertAlmostEqual(
            pya2_contract.functions.balanceOf(owner).call(), owner_balance_expected
        )
        self.assertAlmostEqual(
            pya2_contract.functions.balanceOf(pya_contract.address).call(), pya_balance_expected
        )

        # test recover without owner permission
        # w3.eth.default_account = w3.eth.accounts[2]
        # test recover amount over balance
        # amount = pya2_contract.functions.balanceOf(pya_contract.address).call() + 1

        # Recovering
        owner_balance = pya2_contract.functions.balanceOf(owner).call()
        owner_balance_expected = owner_balance + amount
        pya_balance = pya2_contract.functions.balanceOf(pya_contract.address).call()
        pya_balance_expected = pya_balance - amount
        pya_contract.functions.recoverToken(pya2_contract.address, amount).transact()

        # Debugging
        if debugging:
            print(f"""
            After Recover
            ---------------
            owner_balance: {to_ether(owner_balance)}
            owner_balance_expected: {to_ether(owner_balance_expected)}
            pya_balance: {to_ether(pya_balance)}
            pya_balance_expected: {to_ether(pya_balance_expected)}
            """)

        self.assertAlmostEqual(
            pya2_contract.functions.balanceOf(owner).call(), owner_balance_expected
        )
        self.assertAlmostEqual(
            pya2_contract.functions.balanceOf(pya_contract.address).call(), pya_balance_expected
        )

    @staticmethod
    def __send_transaction(tx_data: dict):
        tx = {
            'from': w3.eth.default_account,
            'to': tx_data['to'],
            'value': tx_data['value'],
            'data': tx_data['data'],
            'nonce': w3.eth.get_transaction_count(w3.eth.default_account),
            'gasPrice': w3.eth.gas_price
        }
        tx.update({'gas': w3.eth.estimate_gas(tx)})
        tx_hash = w3.eth.send_transaction(tx)
        transaction = w3.eth.get_transaction(tx_hash)
        transaction_receipt = w3.eth.get_transaction_receipt(tx_hash)

        if debugging:
            print(f"""
            tx_hash: {tx_hash}
            transaction: {transaction}
            transaction_receipt: {transaction_receipt}
            """)


if __name__ == '__main__':
    unittest.main()
