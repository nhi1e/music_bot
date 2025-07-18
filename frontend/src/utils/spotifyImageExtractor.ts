import { SpotifyImage } from "@/types";

export const extractSpotifyImages = (responseText: string) => {
	console.log("Extracting Spotify images from response:", responseText);
	console.log("Response text length:", responseText.length);

	const images: SpotifyImage[] = [];
	let cleanedText = responseText;

	try {
		// Look for markdown image patterns to extract URLs and remove from text
		const markdownImagePatterns = [
			/!\[.*?\]\((https:\/\/[^)]+)\)/g,
			/!\[Artist:.*?\]\((https:\/\/[^)]+)\)/g,
			/!\[Track:.*?\]\((https:\/\/[^)]+)\)/g,
			/!\[Album:.*?\]\((https:\/\/[^)]+)\)/g,
		];

		const foundUrls: string[] = [];
		const markdownMatches: string[] = [];

		markdownImagePatterns.forEach((pattern, index) => {
			console.log(`Testing markdown pattern ${index + 1}:`, pattern.source);
			const matches = responseText.match(pattern);
			console.log(`Pattern ${index + 1} matches:`, matches);
			if (matches) {
				markdownMatches.push(...matches);
				const urlMatches = matches
					.map((match) => {
						console.log("Processing match:", match);
						const urlMatch = match.match(/\(([^)]+)\)/);
						console.log("Extracted URL:", urlMatch ? urlMatch[1] : null);
						return urlMatch ? urlMatch[1] : null;
					})
					.filter((url): url is string => url !== null);
				foundUrls.push(...urlMatches);
			}
		});

		// Remove all markdown image syntax from the text
		markdownMatches.forEach((match) => {
			cleanedText = cleanedText.replace(match, "").replace(/\n\n\n/g, "\n\n");
		});

		// Also look for direct Spotify URLs (fallback)
		const directUrlPatterns = [
			/https:\/\/i\.scdn\.co\/image\/[a-f0-9]{32}/g,
			/https:\/\/mosaic\.scdn\.co\/640\/[a-f0-9]{32}/g,
			/https:\/\/lineup-images\.scdn\.co\/[^"'\s]+/g,
			/https:\/\/.*\.spotifycdn\.com\/[^"'\s]+/g,
		];

		directUrlPatterns.forEach((pattern) => {
			const matches = responseText.match(pattern);
			if (matches) {
				foundUrls.push(...matches);
			}
		});

		console.log("Found image URLs:", foundUrls);

		if (foundUrls.length > 0) {
			// Remove duplicates and limit to 5 images
			const uniqueUrls = foundUrls.filter(
				(url, index) => foundUrls.indexOf(url) === index
			);
			const limitedUrls = uniqueUrls.slice(0, 5);

			console.log("Processing unique URLs:", limitedUrls);

			limitedUrls.forEach((url, index) => {
				console.log(`Processing URL ${index + 1}:`, url);

				// Try to determine the type based on URL patterns
				let type: "album" | "artist" | "playlist" | "track" = "album";

				if (url.includes("mosaic")) {
					type = "playlist";
					console.log("Detected playlist type");
				} else if (url.includes("lineup-images")) {
					type = "artist";
					console.log(" Detected artist type");
				} else if (url.includes("i.scdn.co")) {
					// Check the original response to see if this was an artist or track image
					const urlIndex = responseText.indexOf(url);
					if (urlIndex !== -1) {
						const contextBefore = responseText.substring(
							Math.max(0, urlIndex - 100),
							urlIndex
						);
						if (contextBefore.includes("Artist:")) {
							type = "artist";
							console.log("Detected artist type from context");
						} else if (contextBefore.includes("Track:")) {
							type = "track";
							console.log("Detected track type from context");
						}
					}
				}

				images.push({ url, type });
				console.log(
					`Added image: type=${type}, url=${url.substring(0, 50)}...`
				);
			});
		} else {
			console.log("No image URLs found in response");
		}

		console.log("Final extracted images:", images);
		console.log("Cleaned text:", cleanedText);
	} catch (error) {
		console.error("Error extracting Spotify images:", error);
	}

	return { images, cleanedText };
};
