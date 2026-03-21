[out:json][timeout:30];
area["name:en"="Nakagawa Ward"]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["amenity"~"pharmacy"](area.inner)(area.outer);
);
out geom;
