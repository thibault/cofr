# Cofr, a way to store encrypted text easily

Use your Trezor to keep your secrets really secrets.

## Warning

This code is **not** officially supported by SatoshiLabs (the company behind
Trezor).

This software comes with absolutely no warantee of any kind. Use it at your own
risk. See the [complete license](LICENSE.md).

## What is it?

Cofr is a tool that lets you use your [Trezor hardware
wallet](https://trezor.io/) to easily encrypt and store some simple pieces of
data.

One might say Cofr is the equivalent of [SotoshiLabs' official password
manager](https://trezor.io/passwords/), with the following differences:

 * you can use it to safekeep any piece of text, not just passwords;
 * it's a standalone console script, it does not come with any graphical
   interface;
 * you don't have to connect to Dropbox or Google drive to use it;
 * you can store data in a single file or multiple files;

## Basic usage

Let's say you have a very private piece of information that you want to protect
at all costs. For example, you bought some [$nano](https://nano.org), a
cryptocurrency that is not supported by Trezor at the moment, and you want to
backup your wallet seed.

Here is how you would do it:

    cofr -f ~/Dropbox/crypto.db set NANO

You will be requested to enter the data you want to backup (your wallet seed),
then to manually confirm action on the Trezor itself.

Your value will then be encrypted and stored in the file
`~/Dropbox/cryptod.db`.

Here, `NANO` is the « key » that you must use to retrieve your value. You can
store different values using different keys.

To get back the value, use the reverse command using the same key:

    cofr -f ~/Dropbox/crypto.db get NANO

To list all keys defined in a file:

    cofr -f ~/Dropbox/crypto.db list

To erase an existing key:

    cofr -f ~/Dropbox/crypto.db rm NANO

For safety reasons, it is not possible to update a key's value. You must first
erase it an create it anew.


## Installation

Work in progress.


## Usage

For usage information, use:

    cofr --help

For detailed usage about a command, use:

    cofr <command> --help


## Safety considerations

**PLEASE READ THIS OR YOUR FUNDS WILL GET STOLEN.** We will not be held
responsible if anything bad happens to you because your usage of this tool.

Cofr implements a variation of [SatoshiLab's SLIP-0016 format for password
storage and
encryption](https://github.com/satoshilabs/slips/blob/master/slip-0016.md),
meaning that it uses the exact same way of encryption that is used in the
official Trezor password manager.

Your secrets are encrypted, then stored in a encrypted file. This file SHOULD
be safe to backup anywhere (Dropbox, Google Drive, etc.)

### Ways you could lose your data

Here is a list of events that might lead to you **completely** and
**irreversibly** losing access to your secret data:

 * The db file is erased or lost and you don't have any backup.
 * Your Trezor is lost / stolen / damaged and you don't have a backup of the
   Trezor seed.

### Ways your data could be leaked

Here is a list of events that might lead to a leak of your secret data, causing
an eventual theft of your funds:

 * Your secret data was generated and or handled *before encryption* on an
   unsafe computer hosting a malware / spyware / keylogger / etc.
 * Your Trezor seed is leaked.

Cofr uses mathematically proven encryption methods, but if you use a tool to
handle highly sensitive data on an unsafe computer, the amount of protection
you receive is None.


## Where does the name comes from?

In french, *un coffre* is a safe. Hence, Cofr. Do you know how hard it is to
find good and available project names?
