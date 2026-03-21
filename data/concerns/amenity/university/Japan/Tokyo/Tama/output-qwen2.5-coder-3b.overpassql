[out:json][timeout:30];
area["name:ja"="東京都"]->.outer;
area["name:ja"="港区"]->.inner;
(
  nwr["amenity"~"university"](area.inner)(area.outer);
);
out geom;
