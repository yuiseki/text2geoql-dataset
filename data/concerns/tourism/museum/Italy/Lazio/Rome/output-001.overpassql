[out:json][timeout:30];
area["name:en"="Lazio"]->.outer;
area["name:en"="Rome"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;