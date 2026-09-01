import "@supabase/functions-js/edge-runtime.d.ts";
import { withSupabase } from "@supabase/server";
import Stripe from "npm:stripe@17.0.0";

// this reads the stripe secret key from the function's environment
// variables, we set this up in the supabase dashboard, never hardcoded here
const stripe = new Stripe(Deno.env.get("STRIPE_SECRET_KEY") ?? "", {
  apiVersion: "2024-06-20",
});

export default {
  fetch: withSupabase({ auth: ["publishable"] }, async (req, ctx) => {
    if (req.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }

    try {
      const { type, description, amount, successUrl, cancelUrl, metadata } =
        await req.json();

      // amount comes in as whole dollars from the frontend, stripe expects
      // the smallest currency unit (cents), so we multiply by 100
      const session = await stripe.checkout.sessions.create({
        mode: "payment",
        payment_method_types: ["card"],
        line_items: [
          {
            price_data: {
              currency: "usd",
              product_data: {
                name: description,
              },
              unit_amount: Math.round(amount * 100),
            },
            quantity: 1,
          },
        ],
        success_url: successUrl,
        cancel_url: cancelUrl,
        // metadata lets us pass through booking/service details so we
        // know what this payment was for once stripe redirects back
        metadata: metadata,
      });

      return Response.json({ url: session.url, sessionId: session.id });
    } catch (error) {
      console.error("Stripe session creation error:", error);
      return Response.json({ error: error.message }, { status: 400 });
    }
  }),
};