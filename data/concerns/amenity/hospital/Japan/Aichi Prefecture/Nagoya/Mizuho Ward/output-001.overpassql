[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Mizuho Ward"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
