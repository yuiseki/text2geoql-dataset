[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Higashinari Ward"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
