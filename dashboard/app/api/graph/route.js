import { getGraphData } from '../../../lib/db';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const graph = getGraphData();
    return NextResponse.json(graph);
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
