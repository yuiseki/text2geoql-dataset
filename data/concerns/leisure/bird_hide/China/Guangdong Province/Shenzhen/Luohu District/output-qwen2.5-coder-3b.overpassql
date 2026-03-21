[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["leisure"~"bird_hide"](area.inner)(area.outer);
);
out geom;
