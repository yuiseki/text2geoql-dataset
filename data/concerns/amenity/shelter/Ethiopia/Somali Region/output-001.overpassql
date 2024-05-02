[out:json][timeout:30000];
area["name:en"="Ethiopia"]->.outer;
area["name:en"="Somali Region"]->.inner;
(
  nwr["amenity"="shelter"](area.inner)(area.outer);
  nwr["amenity"="refugee_site"](area.inner)(area.outer);
);
out geom;
