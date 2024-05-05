// Important note: Never use "amenity"="mosque". It is wrong. Use "building"="mosque" and/or "amenity"="place_of_worship" and "religion"="muslim" instead.
[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Ota"]->.inner;
(
  nwr["building"="mosque"](area.inner)(area.outer);
  nwr["amenity"="place_of_worship"]["religion"="muslim"](area.inner)(area.outer);
);
out geom;
