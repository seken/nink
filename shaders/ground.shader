#version 120

vertex:
	attribute vec2 texCoord;
	attribute vec3 position;
	
	uniform mat4 mvp;
	
	varying vec2 texCoordFrag;
	varying vec3 positionFrag;
	
	void main() {
		texCoordFrag = texCoord;
		positionFrag = position;
		gl_Position = mvp * vec4(position, 1);
	}
	
fragment:
	varying vec2 texCoordFrag;
	varying vec3 positionFrag;
	
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
		float tile = floor(texture2D(map, texCoordFrag).r * (tAmount-1));
		vec2 tileUV = vec2((mod(texCoordFrag.x, resX)/resX)/tNumX, (mod(texCoordFrag.y, resY)/resY)/tNumY);
		float u = mod(tile, tNumX)/tNumX;
		float v = (floor(tile / tNumX)+1)/tNumY;
		tileUV = tileUV+vec2(u, v);
		vec4 tileColour = texture2D(tiles, tileUV);
		gl_FragColor = tileColour*vec4(vec3(playerLight), 1)*clamp(-log2(length(positionFrag - playerPosition)/16), 0.0, 1.0);
	}