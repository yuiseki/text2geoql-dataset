[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["amenity"~"restaurant"](area.inner)(area.outer);
);
out geom;
