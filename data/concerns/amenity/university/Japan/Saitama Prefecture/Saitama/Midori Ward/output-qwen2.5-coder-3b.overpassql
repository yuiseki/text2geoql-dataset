[out:json][timeout:30];
area["name:ja"="みどり市"]->.outer;
area["name:en"="Midori"]->.inner;
(
  nwr["amenity"="university"](area.inner)(area.outer);
);
out geom;
