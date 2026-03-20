[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Kanazawa Ward"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
