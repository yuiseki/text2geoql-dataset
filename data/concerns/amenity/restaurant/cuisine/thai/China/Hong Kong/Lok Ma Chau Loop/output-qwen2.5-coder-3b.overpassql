[out:json][timeout:30];
area["name:zh"="香港"]->.outer;
(
  nwr["cuisine"~"thai"](area.outer);
);
out geom;
