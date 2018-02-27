# Cofr, safely backup your sensitive data

Cofr is a tool to easily and safely use your Trezor hardware wallet to keep
your sensitive data encrypted.

Cofr data files are perfectly safe to backup on Dropbox, Google Drive or any
other cloud service.

Here's an usage example where I'm saving some cryptocurrency wallet seed:

    $ cofr -f ~/Dropbox/important_data.db
    The given file does not exist. Do you wish to create it? [y/N]: y
    Please, confirm store decryption on the device.

    Welcome to the Cofr shell. Type help or ? for command list.

    This software comes with NO WARRANTY whatsoever. Use it at your own risk.
    Make sure to **backup** your store file.

    Cofr> put nano_wallet_seed
    Please, provide the value for key "nano_wallet_seed": e217e2727ba080bf9fbab9c93bd8ba71eeecef3cac1dcb64c0ce4d7908712561
    Done!
    Cofr> sync
    Changes written back to disk.
    Cofr> quit
    Bye!

## Warning

This code is **not** officially supported by SatoshiLabs (the company behind
Trezor).

This software is provided "as is" and comes with absolutely no warantee of any
kind. Use it at your own risk. See the [complete license](LICENSE.md).

## What is it?

Cofr is a tool that lets you use your [Trezor hardware
wallet](https://trezor.io/) to easily store some simple pieces of text in
encrypted data files.

One might say Cofr is an equivalent of [SotoshiLabs' official password
manager](https://trezor.io/passwords/), with the following differences:

 * you can use it to safekeep any piece of text, not just passwords;
 * it's a standalone console script, it does not come with any graphical
   interface;
 * you don't have to connect to Dropbox or Google drive to use it;
 * you can store data in a single file or multiple files;

## Usage

Let's say you have a very private piece of information that you want to protect
at all costs. For example, you bought some [$NANO](https://nano.org), a
cryptocurrency that is not supported by Trezor at the moment, and you want to
backup your wallet seed.

### Storing data

Make sure your Trezor is plugged, then type in a shell:

    cofr -f ~/Dropbox/crypto.db

If the file does not already exists, you will be prompted for confirmation. You
also need to physically activate the file encryption on the Trezor.

Once this is done, you get access to the Cofr shell.

    Cofr>

Type in your commands to read existing data, or add new data in the store.

Here is the list of available commands:

 * `list`: List all keys in the file.
 * `put`: Store a new key / value in the file.
 * `get`: Display a specific value.
 * `del`: Removes a key from the file.
 * `sync`: Writes changes back to disk.
 * `quit`: Exits the shell.

To store new data in the Cofr file, use the `put` command:

    Cofr> put nano_wallet_seed
    Please, provide the value for key "nano_wallet_seed": e217e2727ba080bf9fbab9c93bd8ba71eeecef3cac1dcb64c0ce4d7908712561
    Done!

**Please note that nothing will happen until you actually commit the changes
to the Cofr file using the `sync` command.**

    Cofr> sync
    Changes written back to disk.

You can then safely exit Cofr:

    Cofr> quit
    Bye!

### Retrieving data

Time for data retrieval. Start Cofr and give the Cofr file as a parameter, like
you did before. Once again, you will have to manually confirm the file
decryption on the Trezor.

Then, use the `list` command to see existing keys in the Cofr file, or retrieve
the value associated with a key using the `get` command:

    Cofr> get nano_wallet_seed
    Please, confirm key decryption on the device.
    e217e2727ba080bf9fbab9c93bd8ba71eeecef3cac1dcb64c0ce4d7908712561

## Installation

Work in progress.


## Data safety, encryption, technical information

Cofr uses a double level of encryption to make sure your data is safe. First,
each value is individually encrypted *then*, the complete file is encrypted
before being stored on disk.

It means that even if an attacker could get access to the Cofr data file, they
would not be able to decrypt the data unless they also get their hand on your
**Trezor wallet seed**. Cofr data files are perfectly safe to backup on
Dropbox, Google Drive or any other cloud service, even unencrypted ones.

The encryption used by Cofr is very similar to the one used in SatoshiLab's
password manager, and [described in this
document](https://github.com/satoshilabs/slips/blob/master/slip-0016.md).

In short, Cofr uses the Trezor to generate deterministic encryption keys, and
then uses those keys to encrypt your data with AES-GCM.


## Safety considerations

**PLEASE READ THIS OR YOUR FUNDS WILL GET STOLEN.** We will not be held
responsible if anything bad happens to you because your usage of this tool.

### Ways you could lose your data

For information purpose, here is a list of events that might lead to you
**completely** and **irreversibly** losing access to your secret data:

 * The Cofr data file is erased or lost and you don't have any backup.
 * Your Trezor is lost / stolen / damaged and you don't have a backup of the
   Trezor seed.

To mitigate those issues:

 * Make several backups of the data files, e.g in Dropbox or subscribe to a
   cloud-based backup service.
 * Take every measure to make sure your Trezor seed is safe.

### Ways your data could be leaked

Here is a list of events that might lead to a leak of your secret data, causing
an eventual theft of your funds:

 * Your secret data was generated and or handled *before encryption* on an
   unsafe computer hosting a malware / spyware / keylogger / etc.
 * Your Trezor seed is leaked.
 * Some malicious hacker hijacked my computer and uploaded a modified version
   of Cofr designed to discretely upload data to a remote server.
 * I'm a malicious hacker trying to scam you.

To mitigate those issues:

 * Only manipulate sensitive data on safe and trusted computers, e.g computers
   unplugged from the internet and booted on a [live linux
   system](https://tails.boum.org/).
 * Trust no one, and inspect the source code yourself. Ask people you trust to
   do the same.

Cofr uses mathematically proven encryption methods, but if you use a tool to
handle highly sensitive data on an unsafe computer, the amount of protection
you receive is None.

## Where does the name comes from?

In french, *un coffre* is a safe. Hence, Cofr. Do you know how hard it is to
find good and available project names?
