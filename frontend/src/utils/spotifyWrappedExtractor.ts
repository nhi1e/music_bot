import { SpotifyWrappedData } from "@/types";

/**
 * Extracts Spotify Wrapped data from an AI response containing JSON data
 */
export function extractSpotifyWrappedData(
	content: string
): SpotifyWrappedData | null {
	console.log("Extracting Spotify Wrapped data from content:");
	console.log("Content length:", content.length);
	console.log("Content preview:", content.substring(0, 500));

	// Check if the marker exists
	const hasMarker = content.includes("SPOTIFY_WRAPPED_DATA:");
	console.log("Has SPOTIFY_WRAPPED_DATA marker:", hasMarker);

	if (!hasMarker) {
		console.log("No SPOTIFY_WRAPPED_DATA marker found");
		return null;
	}

	// Find the marker position
	const markerIndex = content.indexOf("SPOTIFY_WRAPPED_DATA:");
	console.log("Marker found at index:", markerIndex);

	// Extract everything after the marker
	const afterMarker = content.substring(
		markerIndex + "SPOTIFY_WRAPPED_DATA:".length
	);
	console.log("Content after marker:", afterMarker.substring(0, 200));

	// Try different regex patterns
	const patterns = [
		/^\s*(\{[\s\S]*?\})/, // Match any JSON object
		/^\s*(\{.*\})/m, // Multiline match
		/(\{[\s\S]*\})/, // Simple greedy match
	];

	for (let i = 0; i < patterns.length; i++) {
		const match = afterMarker.match(patterns[i]);
		console.log(`Pattern ${i + 1} match:`, match ? "found" : "not found");

		if (match && match[1]) {
			try {
				console.log(`Raw JSON string from pattern ${i + 1}:`, match[1]);
				const parsedData = JSON.parse(match[1].trim());
				console.log("Successfully parsed data:", parsedData);
				return parsedData;
			} catch (error) {
				console.error(`Error parsing with pattern ${i + 1}:`, error);
			}
		}
	}

	console.log("No patterns matched successfully");
	return null;
}

/**
 * Checks if a user message is requesting a Spotify Wrapped
 */
export function isSpotifyWrappedRequest(message: string): boolean {
	const wrappedKeywords = [
		"wrapped",
		"spotify wrapped",
		"year in review",
		"my year",
		"annual summary",
		"music summary",
		"yearly recap",
	];

	const lowerMessage = message.toLowerCase();
	return wrappedKeywords.some((keyword) => lowerMessage.includes(keyword));
}

/**
 * Gets the appropriate time range based on user request
 */
export function getTimeRangeFromMessage(message: string): string {
	const lowerMessage = message.toLowerCase();

	if (lowerMessage.includes("month") || lowerMessage.includes("recent")) {
		return "short_term"; // Last 4 weeks
	} else if (
		lowerMessage.includes("6 months") ||
		lowerMessage.includes("half year")
	) {
		return "medium_term"; // Last 6 months
	} else {
		return "long_term"; // All time (default for "this year" etc)
	}
}

/**
 * Gets friendly timeframe label for display
 */
export function getTimeframeLabel(timeRange: string): string {
	switch (timeRange) {
		case "short_term":
			return "Last 4 Weeks";
		case "medium_term":
			return "Last 6 Months";
		case "long_term":
		default:
			return "This Year";
	}
}
