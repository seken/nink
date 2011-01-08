#version 120

vertex:
	attribute vec2 texCoord;
	attribute vec3 position;
	attribute float tile;
	
	uniform mat4 mvp;
	
	varying vec2 texCoordFrag;
	varying vec3 positionFrag;
	varying float tileFrag;
	
	void main() {
		texCoordFrag = texCoord;
		positionFrag = position;
		tileFrag = tile;
		gl_Position = mvp * vec4(position, 1);
	}
	
fragment:
	varying vec2 texCoordFrag;
	varying vec3 positionFrag;
	varying float tileFrag;
	
	uniform sampler2D map;
	uniform sampler2D tiles;
	
	uniform float tNumX;
	uniform float tNumY;
	uniform float tAmount;
	uniform float resX;
	uniform float resY;
	
	uniform vec3 playerPosition;
	uniform float playerLight;
	
	void main() {
		float tile = tileFrag;
		float u = mod(tile, tNumX)/tNumX;
		float v = (floor(tile / tNumX)+1)/tNumY;
		vec2 tileUV = vec2(u, v) + vec2(texCoordFrag.x/tNumX, texCoordFrag.y/tNumY);
		vec4 tileColour = texture2D(tiles, tileUV);
		gl_FragColor = tileColour*vec4(vec3(playerLight), 1)*clamp(-log2(length(positionFrag - playerPosition)/16), 0.0, 1.0);
	}