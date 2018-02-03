# ISTS16-ScoringChecks
Scoring checks for ISTS 16


## Command Center Check
Arguments
    - address

Example:
`python check.py -a address`

## Ecommerce Check
Arguments
    - address
    - team

Example
`python check.py -t 1 -a address`

## Jenkins Check
Arguments
    - address
    - password

Example:
`python vars.py address password`

## SMB Check
Arguments
    - address
    - username
    - password
    - hash(file hash to compare)

Example:
`python smb_check.py --host address --user username --pass password --hash filehash`
