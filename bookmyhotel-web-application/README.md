# BookMyHotel

A full-stack hotel booking platform built for a Dubai-based operator managing four five-star hotels (Marriott Dubai, Hilton Paris, Hyatt Tokyo, Four Seasons Santorini).

**Module:** SWE6013 Enterprise Systems Development

**Student:** Daniel Agbonmeire Oyakhire

**Student Number:** 2533954

**Live Deployment:** https://bookmyhotel-2533954.netlify.app/

---

## Tech Stack

* **Frontend:** React.js (Vite)
* **Backend / Database:** Supabase (PostgreSQL, Auth, Storage, Edge Functions)
* **Payments:** Stripe (Checkout, sandbox/test mode)
* **Hosting:** Netlify
* **Styling:** Plain CSS with a custom design system ("Desert Pearl")
* **Icons:** Lucide React
* **Charts:** Recharts (Admin Analytics)

---

## Project Structure

```
bookmyhotel/
├── public/
│   └── _redirects          # Netlify SPA routing fix
├── src/
│   ├── components/         # Navbar, Footer, ReviewSection, HotelCard, etc.
│   ├── context/             # AuthContext (auth + admin state)
│   ├── pages/               # Home, Hotels, HotelDetail, BookingForm, etc.
│   │   └── admin/           # Admin dashboard pages
│   └── utils/                # Supabase client setup
├── supabase/
│   └── functions/           # Edge Functions (Stripe checkout + verification)
└── package.json
```

---

## Core Features (Functional Requirements)

1. User registration with email confirmation
2. Secure login/logout
3. Search and filter hotels by name, city, country, price, facilities, services, and room type
4. Detailed hotel information pages, including guest reviews and sustainability info
5. Room reservation with live date/price calculation
6. Booking cancellation (guest and admin)
7. Real-time availability checking by date, with conflict prevention
8. Additional paid hotel services, addable at booking or afterward
9. Contact form with admin inbox
10. Promotional discount codes, applied at checkout
11. Guest reviews, restricted to verified bookings
12. Admin CRUD for hotels
13. Admin management of reservations, with date and reference search
14. Admin analytics dashboard (bookings, revenue, cancellation rate)
15. Secure payment processing via Stripe, supporting multiple payment methods (card, Link)
16. Booking confirmation with reference number, tied to verified payment
17. Sustainability information per hotel

---

## Running Locally

1. Clone/extract the project and run:

```
   npm install
   ```

2. Create a `.env` file in the project root with:

```
   VITE_SUPABASE_URL=your_supabase_project_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

3. Start the dev server:

```
   npm run dev
   ```

4. Visit `http://localhost:5173`

**Note:** The Supabase database (tables, RLS policies, Edge Functions) and Stripe test keys are already configured on the live Supabase project this code connects to. Running locally uses the same backend as the live deployment. Since these credentials are not included in this repository, this project is intended to be reviewed via the live deployment link above rather than run locally by others.

---

## Database

Built on Supabase (PostgreSQL) with Row Level Security enabled on every table. Key tables:

* `hotels`, `rooms` — core inventory
* `users` — extends Supabase Auth with profile data and admin flag
* `bookings` — reservations, linked to promotions and tracked by status (pending/confirmed/cancelled)
* `services`, `booking_services` — paid add-ons per hotel, linked to bookings
* `promotions` — discount codes with expiry and active/inactive state
* `reviews` — guest reviews, restricted to users with a completed booking at that hotel
* `contact_messages` — Contact form submissions

A `public_profiles` view exposes only `id` and `full_name` for public display (e.g. reviewer names), keeping email and admin status protected.

---

## Payments

Stripe Checkout is used for both initial room bookings and services added after booking. Two Supabase Edge Functions handle this securely server-side:

* `create-checkout-session` — creates a Stripe Checkout Session for a booking or service
* `verify-payment` — confirms a session's payment status directly with Stripe before a booking is marked confirmed or a service is recorded, rather than trusting the browser redirect alone

Test card for successful payment: `4242 4242 4242 4242`
Test card for a declined payment: `4000 0000 0000 0002`
(Any future expiry date, any 3-digit CVC)

---

## Known Limitations / Future Enhancements

* Automated email notifications for booking confirmations, cancellations, and service additions are not yet implemented
* Two-factor authentication, automated threat monitoring, and rate limiting on authentication endpoints are not yet implemented
* No multilingual support
* No real-time room availability notification system
* No loyalty/rewards programme


