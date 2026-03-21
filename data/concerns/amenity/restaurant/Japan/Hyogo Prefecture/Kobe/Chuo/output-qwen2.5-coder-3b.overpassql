[out:json][timeout:30];
area["name:en"="Kobe"]->.outer;
area["name:en"="Hyogo Prefecture"]->.inner;
(
  nwr["amenity"~"restaurant"](area.inner)(area.outer);
);
out geom;
