#version 120

vertex:
	attribute vec3 normal;
	attribute vec2 texCoord;
	attribute vec3 position;
	
	uniform mat4 mvp;
	
	varying vec2 texCoordFrag;
	varying vec3 positionFrag;
	varying vec3 normalFrag;
	
	void main() {
		texCoordFrag = texCoord;
		positionFrag = position;
		normalFrag = normal;
		gl_Position = mvp * vec4(position, 1);
	}
	
fragment:
	varying vec2 texCoordFrag;
	varying vec3 positionFrag;
	varying vec3 normalFrag;
	
	uniform sampler2D tex;
	uniform vec3 playerPosition;
	uniform float playerLight;
	
	uniform mat4 modelview;
	
	void main() {
		gl_FragColor = texture2D(tex, texCoordFrag)*vec4(vec3(playerLight), 1)*clamp(-log2(length((modelview*vec4(positionFrag, 1.0)).rgb - playerPosition)/16), 0.0, 1.0);
	}