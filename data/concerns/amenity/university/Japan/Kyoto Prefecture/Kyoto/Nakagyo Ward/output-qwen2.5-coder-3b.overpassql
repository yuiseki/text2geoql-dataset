[out:json][timeout:30];
area["name:ja"="京都府"]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["amenity"="university"](area.inner)(area.outer);
);
out geom;
