// Important note: Never use "amenity"="mosque". It is wrong. Use "building"="mosque" and/or "amenity"="place_of_worship" and "religion"="muslim" instead.
[out:json][timeout:30000];
area["name:en"="Tokyo"]->.searchArea;
(
  nwr["building"="mosque"](area.searchArea);
  nwr["amenity"="place_of_worship"]["religion"="muslim"](area.searchArea);
);
out geom;
