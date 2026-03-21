[out:json][timeout:30];
area["name:en"="Hodogaya Ward"]->.outer;
area["name:ja"="横浜市"]->.inner;
(
  nwr["craft"~"pottery"](area.inner)(area.outer);
);
out geom;
