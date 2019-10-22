/* global escher, d3, GLP_FX, glp_set_row_bnds, glp_set_row_name, glp_add_cols,
 glp_add_rows, GLP_MAX, glp_set_obj_dir, glp_set_prob_name, glp_create_prob,
 glp_get_obj_val, glp_simplex, GLP_ON, SMCP, glp_load_matrix, glp_set_obj_coef,
 GLP_DB, glp_set_col_bnds, glp_set_col_name, glp_get_col_name, glp_get_col_prim,
 glp_get_obj_val, glp_get_num_cols */

// load everything
// load_builder(function (builder) {
//   load_model(model => {
//     var old_model = escher.utils.clone(model);
//     optimize_loop(builder, model);
//     escher.libs.d3_select('#reset-button')
//       .on('click', () => {
//         model = escher.utils.clone(old_model);
//         optimize_loop(builder, model);
//       });
//   });
// });

function load_builder (callback) {
  // load the Builder
  escher.libs.d3_json('https://foresyn.tech/static/map.json', function(e, data) {
    if (e) console.warn(e);
    var options = {
      menu: 'all',
      enable_editing: false,
      fill_screen: true,
      reaction_styles: ['abs', 'color', 'size', 'text'],
      never_ask_before_quit: true,
      enable_tooltips: false,
      first_load_callback: callback
    };
    var b = escher.Builder(data, null, null, escher.libs.d3_select('#map_container'), options);
  });
}


function load_model(callback, model_json='e_coli_core.json') {
  escher.libs.d3_json(model_json, function(e, data) {
    if (e) console.warn(e);
    callback(data);
  });
}


function set_knockout_status(text) {
  escher.libs.d3_select('#knockout-status').text(text);
}


function optimize_loop (builder, model) {
  var solve_and_display = function(m, knockouts) {
    var problem = build_glpk_problem(m);
    var result = optimize(problem);
    var keys = Object.keys(knockouts),
        ko_string = keys.map(function(s) { return 'Δ'+s; }).join(' ');
    var nbs = String.fromCharCode(160); // non-breaking space
    if (keys.length > 0)
      ko_string += (' (' + keys.length + 'KO): ');
    else ko_string = 'Click a reaction to knock it out. ';
    if (result.f < 1e-3) {
      builder.set_reaction_data(null);
      set_knockout_status(ko_string + 'You killed E.' + nbs + 'coli!');
    } else {
      builder.set_reaction_data(result.x);
      console.log(result.f)
      set_knockout_status(ko_string + 'Growth' + nbs + 'rate:' + nbs +
                          (result.f/0.8739215069684303*100).toFixed(1) + '%');
    }
  };

  var knockouts = {},
      knockable = function(r) {
        return (r.indexOf('EX_') == -1 &&
                r.indexOf('ATPM') == -1 &&
                r.indexOf('BIOMASS') == -1);
      };

  // set up and run
  // model = set_carbon_source(model, 'EX_glc__D_e', 20);
  solve_and_display(model, knockouts);

  // initialize event listeners
  var sel = builder.selection;
  sel.selectAll('.reaction,.reaction-label')
    .style('cursor', function(d) {
      if (knockable(d.bigg_id)) return 'pointer';
      else return null;
    })
    .on('click', function(d) {
      if (knockable(d.bigg_id)) {
        if (!(d.bigg_id in knockouts))
          knockouts[d.bigg_id] = true;
        model = knock_out_reaction(model, d.bigg_id);
        solve_and_display(model, knockouts);
      }
    });
  // grey for reactions that cannot be knocked out
  sel.selectAll('.reaction-label')
    .style('fill', function(d) {
      if (!knockable(d.bigg_id)) return '#888';
      else return null;
    });
}


function fill_array(len, val) {
  for (var i = 0, arr = new Array(len); i < len;)
    arr[i++] = val;
  return arr;
}


function fill_array_single(len, val, index_value, index) {
  for (var i = 0, arr = new Array(len); i < len;) {
    if (i == index)
      arr[i++] = index_value;
    else
      arr[i++] = val;
  }
  return arr;
}


function knock_out_reaction(model, reaction_id) {
  for (var i = 0, l = model.reactions.length; i < l; i++) {
    if (model.reactions[i].id == reaction_id) {
      model.reactions[i].lower_bound = 0.0;
      model.reactions[i].upper_bound = 0.0;
      return model;
    }
  }
  throw new Error('Bad reaction ' + reaction_id);
}


function set_carbon_source(model, reaction_id, sur) {
  for (var i = 0, l = model.reactions.length; i < l; i++) {
    if (model.reactions[i].id == reaction_id) {
      model.reactions[i].lower_bound = -sur;
      return model;
    }
  }
  throw new Error('Bad carbon source ' + reaction_id);
}


function build_glpk_problem (model) {
  /** Build a GLPK LP for the model */

  var nRows = model.metabolites.length;
  var nCols = model.reactions.length;
  var ia = [];
  var ja = [];
  var ar = [];
  var metLookup = {};

  // initialize LP objective
  var lp = glp_create_prob();
  glp_set_prob_name(lp, 'knockout FBA')
  // maximize
  glp_set_obj_dir(lp, GLP_MAX)
  // set up rows and columns
  glp_add_rows(lp, nRows)
  glp_add_cols(lp, nCols)

  // metabolites
  model.metabolites.forEach(function (metabolite, i) {
    var rowInd = i + 1
    glp_set_row_name(lp, rowInd, metabolite.id)
    glp_set_row_bnds(lp, rowInd, GLP_FX, 0.0, 0.0)
    // remember the indices of the metabolites
    metLookup[metabolite.id] = rowInd
  })

  // reactions
  var matInd = 1
  model.reactions.forEach(function (reaction, i) {
    var colInd = i + 1

    glp_set_col_name(lp, colInd, reaction.id)
    if (reaction.lower_bound === reaction.upper_bound) {
      glp_set_col_bnds(lp, colInd, GLP_FX, reaction.lower_bound, reaction.upper_bound)
    } else {
      glp_set_col_bnds(lp, colInd, GLP_DB, reaction.lower_bound, reaction.upper_bound)
    }

    // object_coefficient is optional for reaction in COBRA JSON
    if ('objective_coefficient' in reaction) {
      glp_set_obj_coef(lp, colInd, reaction.objective_coefficient)
    }

    // S matrix values
    for (var met_id in reaction.metabolites) {
      ia[matInd] = metLookup[met_id]
      ja[matInd] = colInd
      ar[matInd] = reaction.metabolites[met_id]
      matInd++
    }
  })
  // Load the S matrix
  glp_load_matrix(lp, ia.length - 1, ia, ja, ar)

  return lp
}


function optimize(problem) {
  var smcp = new SMCP({presolve: GLP_ON});
  var returnCode = glp_simplex(problem, smcp);
  var f = null
  var x = null
  if (returnCode === 0) {
    // get the objective
    f = glp_get_obj_val(problem)
    // get the primal
    x = {}
    for (var i = 1; i <= glp_get_num_cols(problem); i++) {
      x[glp_get_col_name(problem, i)] = glp_get_col_prim(problem, i)
    }
  } else {
    console.error('Invalid Solution')
  }

  return {f: f, x: x};
}
