[out:json][timeout:30000];
area["name:en"="Kobe"]->.outer;
area["name:en"="Hyogo Prefecture"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
