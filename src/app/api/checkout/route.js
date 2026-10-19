export async function POST() {
  return Response.json(
    { error: "Sprinting Ink is free. Payments are no longer accepted." },
    { status: 410 }
  );
}
