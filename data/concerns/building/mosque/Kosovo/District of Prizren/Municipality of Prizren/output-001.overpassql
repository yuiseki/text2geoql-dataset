// Important note: Never use "amenity"="mosque". It is wrong. Use "building"="mosque" instead.
[out:json][timeout:30000];
area["name:en"="Municipality of Prizren"]->.searchArea;
(
  nwr["building"="mosque"](area.searchArea);
);
out geom;
