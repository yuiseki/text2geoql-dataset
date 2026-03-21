[out:json][timeout:30];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["amenity"~"restaurant"](area.inner)(area.outer);
);
out geom;
