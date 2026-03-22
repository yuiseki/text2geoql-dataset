[out:json][timeout:30];
area["name:en"="North Rhine-Westphalia"]->.outer;
area["name:en"="Cologne"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;