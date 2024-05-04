// Important note: Never use "amenity"="church". It is wrong. Use "building"="church" instead.
[out:json][timeout:30000];
area["name:en"="Kyoto Prefecture"]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
