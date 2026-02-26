Module Name: Travel Itinerary
Module: HRMS / HR
Type: Child Table (of Travel Request)
DocStatus: No

Description
A single leg or stop of a travel request itinerary.

Parent
Travel Request (field: itinerary)

Dependencies
None

Schema Fields
departure_date: Date, Optional.
departure_city: Data, Optional.
arrival_date: Date, Optional.
arrival_city: Data, Optional.
mode_of_transport: Select (Airways, Railways, Roadways, Waterways), Optional.
lodging_required: Check, Default: 0.
