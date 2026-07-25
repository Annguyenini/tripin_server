# User Setting Data Shapes

## Return User Setting Shape

```ts
type ReturnUserSetting = {
  has_seen_onboarding: boolean;
  language: string;
  updated_at: number; // Unix timestamp in milliseconds
  user_id: number;
};
```

## Stored User Setting Shape

```ts
type StoredUserSetting = {
  has_seen_onboarding: boolean;
  language: string;
  updated_at: timestamptz;
  user_id: number;
};
```

# Field Descriptions

| Field | Description |
|---------|-------------|
| `has_seen_onboarding` | Indicates whether the user has completed or viewed the onboarding flow. |
| `language` | User's preferred language setting. |
| `updated_at` | Timestamp updated whenever the user's settings are modified. |
| `user_id` | Identifier of the user associated with these settings. |
