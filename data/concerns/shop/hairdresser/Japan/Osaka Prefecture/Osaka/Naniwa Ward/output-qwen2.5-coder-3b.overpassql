[out:json][timeout:30];
area["name:en"="Osaka"][boundary=administrative]->.outer;
area["name:en"="Osaka Prefecture"]->.inner;
(
  nwr["amenity"="hairdresser"](area.inner)(area.outer);
);
out geom;
