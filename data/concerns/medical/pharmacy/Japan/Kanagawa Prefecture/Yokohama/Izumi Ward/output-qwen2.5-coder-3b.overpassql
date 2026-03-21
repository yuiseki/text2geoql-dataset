[out:json][timeout:30];
area["name:en"="Izumi Ward"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["amenity"~"pharmacy"](area.inner)(area.outer);
);
out geom;
