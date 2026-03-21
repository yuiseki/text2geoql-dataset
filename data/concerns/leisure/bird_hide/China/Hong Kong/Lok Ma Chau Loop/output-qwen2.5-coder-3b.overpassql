[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["leisure"~"bird_hide"](area.outer);
);
out geom;
