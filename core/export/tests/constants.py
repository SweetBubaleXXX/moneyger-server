EXPORTED_CATEGORIES = [
    {
        "transaction_type": "IN",
        "name": "Category 1",
        "display_order": 1,
        "icon": "default",
        "color": "#123456",
        "subcategories": [
            {
                "transaction_type": "IN",
                "name": "Subcategory 1",
                "display_order": 1,
                "icon": "default",
                "color": "#123456",
                "subcategories": [
                    {
                        "transaction_type": "IN",
                        "name": "Subcategory 1.1",
                        "display_order": 1,
                        "icon": "default",
                        "color": "#123456",
                        "subcategories": [],
                        "transactions": [
                            {
                                "currency": "EUR",
                                "amount": 240,
                                "transaction_time": "2023-09-25T05:16:00Z",
                                "comment": "",
                            },
                            {
                                "currency": "USD",
                                "amount": 300,
                                "transaction_time": "2023-10-01T12:30:00Z",
                                "comment": "Notes",
                            },
                        ],
                    },
                    {
                        "transaction_type": "IN",
                        "name": "Subcategory 1.2",
                        "display_order": 2,
                        "icon": "default",
                        "color": "#123456",
                        "subcategories": [],
                        "transactions": [],
                    },
                    {
                        "transaction_type": "IN",
                        "name": "Subcategory 1.3",
                        "display_order": 3,
                        "icon": "default",
                        "color": "#123456",
                        "subcategories": [],
                        "transactions": [],
                    },
                ],
                "transactions": [],
            },
            {
                "transaction_type": "IN",
                "name": "Subcategory 2",
                "display_order": 2,
                "icon": "default",
                "color": "#123456",
                "subcategories": [],
                "transactions": [],
            },
            {
                "transaction_type": "IN",
                "name": "Subcategory 3",
                "display_order": 3,
                "icon": "default",
                "color": "#123456",
                "subcategories": [],
                "transactions": [],
            },
        ],
        "transactions": [],
    },
    {
        "transaction_type": "OUT",
        "name": "Category 2",
        "display_order": 1,
        "icon": "default",
        "color": "#123456",
        "subcategories": [],
        "transactions": [
            {
                "currency": "BYN",
                "amount": 20,
                "transaction_time": "2023-09-25T05:12:00Z",
                "comment": "",
            },
            {
                "currency": "USD",
                "amount": 3.0,
                "transaction_time": "2023-10-01T12:40:00Z",
                "comment": "",
            },
        ],
    },
]