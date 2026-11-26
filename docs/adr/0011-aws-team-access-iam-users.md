# 0011: Team AWS access with IAM users, MFA and a scoped sandbox

- **Status:** Proposed (for review on 2026-11-26)
- **Date:** 2026-11-25

## Context

Members want to build Lambdas in the club's AWS account (`data-klub-lab`, eu-central-1) and send
files to Databricks. House_Prices itself doesn't need AWS (ADR 0009), so this is a shared
experiment space, and it must stay free and safe: nobody should be able to run up a bill, see
billing, or change other people's access.

## Options

1. **IAM Identity Center (single sign-on):** the standard in companies, with short-lived
   credentials. Giving it access to the account needs AWS Organizations, and enrolling a Free plan
   account in Organizations upgrades it to the Paid plan and ends its Free Tier credits.
2. **One IAM user per member in a group, MFA required, scoped policy:** works on the Free plan,
   and each person has their own login and audit trail. Passwords are long-lived, so MFA matters.
3. **One shared login:** simplest, but no MFA per person, no audit trail, and a leaked password
   exposes everything.

## Decision

Option 2. Members are IAM users in the group `data-klub-team`. Until MFA is on, they can only set
their password and MFA. After that they can manage Lambdas named `dk-*` in eu-central-1 with the
shared role `data-klub-team-lambda`, read `raw/` in the lab bucket, write to their own
`team/<user name>/` folder, and keep their Databricks settings in Parameter Store under
`/data-klub/<user name>/`. No access keys; CloudShell gives them a terminal. The policies and setup
steps are in house-prices-generator `infra/aws-team-access/`.

## Consequences

- A Lambda sends files to Databricks with the Files API (`PUT /api/2.0/fs/files/Volumes/...`),
  because Free Edition can't read the bucket (ADR 0009).
- The account owner creates users and sends temporary passwords by direct message.
- All Lambdas share one execution role, so one member's Lambda could write to another member's
  `team/` folder. Acceptable for a learning group.
- Revisit if the account leaves the Free plan: then Identity Center is the better option.
