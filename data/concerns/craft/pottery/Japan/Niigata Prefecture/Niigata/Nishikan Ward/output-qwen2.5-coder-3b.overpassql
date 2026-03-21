[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Niigata Prefecture"]->.inner;
(
  nwr["craft"~"pottery"](area.inner)(area.outer);
);
out geom;
