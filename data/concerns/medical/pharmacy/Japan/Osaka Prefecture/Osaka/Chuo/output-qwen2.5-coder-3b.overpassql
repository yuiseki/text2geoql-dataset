[out:json][timeout:30];
area["name:en"="Osaka Prefecture"]->.outer;
area["name:en"="Osaka"]->.inner;
(
  nwr["amenity"="pharmacy"](area.inner)(area.outer);
);
out geom;
