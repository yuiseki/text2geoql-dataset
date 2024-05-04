// Important note: Never use "amenity"="church". It is wrong. Use "building"="church" instead.
[out:json][timeout:30000];
area["name:en"="Municipality of Prizren"]->.searchArea;
(
  nwr["building"="church"](area.searchArea);
);
out geom;
